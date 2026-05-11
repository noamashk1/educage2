import ast
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


DEFAULT_DATA_PATH = r"Z:\Shared\Noam\results\asd_juv_06_05_2026\asd_juv_06_05_2026.txt"
MOUSE_COLUMN_CANDIDATES = [
    "MouseName",
    "mouse ID",
    "mouse_id",
    "Mouse",
    "mouse",
    "Animal",
    "Subject",
]
DAY_COLUMN_CANDIDATES = [
    "date",
    "Date",
    "Day",
    "day",
    "SessionDay",
    "session_day",
    "TrainingDay",
    "training_day",
]
OUTCOME_COLUMN_CANDIDATES = ["score", "Score", "Outcome", "outcome", "Outcomes"]


def _read_table(path_or_buffer) -> pd.DataFrame:
    """Try common delimiters and return a DataFrame."""
    separators = [",", "\t", ";", r"\s+"]
    last_error = None
    for sep in separators:
        try:
            df = pd.read_csv(path_or_buffer, sep=sep, engine="python")
            if df.shape[1] > 1:
                return df
        except Exception as exc:  # pragma: no cover - UX fallback
            last_error = exc
    raise ValueError(f"Failed to parse file as table: {last_error}")


def _find_first_existing(columns: pd.Index, candidates: list[str]) -> str | None:
    col_set = set(columns)
    for name in candidates:
        if name in col_set:
            return name
    return None


def _explode_outcomes_if_needed(df: pd.DataFrame, outcome_col: str) -> pd.DataFrame:
    """
    If outcomes are stored as stringified lists (session-level rows),
    explode to one row per trial outcome.
    """
    out = df.copy()
    sample = out[outcome_col].dropna().astype(str).head(20)
    if sample.empty:
        return out

    looks_like_list = sample.str.startswith("[").mean() > 0.5 and sample.str.endswith("]").mean() > 0.5
    if not looks_like_list:
        return out

    def to_list(value):
        if isinstance(value, list):
            return value
        if pd.isna(value):
            return []
        text = str(value).strip()
        if not text:
            return []
        try:
            parsed = ast.literal_eval(text)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            pass
        return [text]

    out[outcome_col] = out[outcome_col].apply(to_list)
    out = out.explode(outcome_col, ignore_index=True)
    return out


def _normalize_day_column(df: pd.DataFrame, day_col: str | None) -> tuple[pd.DataFrame, str]:
    """
    Return DataFrame with numeric day column named 'analysis_day'.
    If no day column is found, create a synthetic day=1.
    """
    out = df.copy()
    if day_col is None:
        out["analysis_day"] = 1.0
        out["analysis_date_label"] = "Day 1"
        return out, "analysis_day"

    numeric_day = pd.to_numeric(out[day_col], errors="coerce")
    if numeric_day.notna().sum() > 0:
        out["analysis_day"] = numeric_day.astype(float)
        out["analysis_date_label"] = numeric_day.apply(
            lambda x: f"Day {int(x)}" if pd.notna(x) and float(x).is_integer() else f"Day {x:.2f}"
        )
        return out, "analysis_day"

    dt = pd.to_datetime(out[day_col], errors="coerce")
    if dt.notna().sum() > 0:
        normalized = dt.dt.normalize()
        unique_dates = sorted(normalized.dropna().unique())
        date_to_idx = {d: i + 1 for i, d in enumerate(unique_dates)}
        out["analysis_day"] = normalized.map(date_to_idx).astype(float)
        out["analysis_date_label"] = normalized.dt.strftime("%Y-%m-%d")
        return out, "analysis_day"

    out["analysis_day"] = 1.0
    out["analysis_date_label"] = "Day 1"
    return out, "analysis_day"


def load_and_prepare(path_or_buffer) -> tuple[pd.DataFrame, str, str]:
    df = _read_table(path_or_buffer)
    if df.empty:
        raise ValueError("Data file is empty.")

    mouse_col = _find_first_existing(df.columns, MOUSE_COLUMN_CANDIDATES)
    if mouse_col is None:
        raise ValueError(
            "Could not find mouse column. Expected one of: "
            + ", ".join(MOUSE_COLUMN_CANDIDATES)
        )

    outcome_col = _find_first_existing(df.columns, OUTCOME_COLUMN_CANDIDATES)
    if outcome_col is None:
        raise ValueError(
            "Could not find outcome column. Expected one of: "
            + ", ".join(OUTCOME_COLUMN_CANDIDATES)
        )

    day_col = _find_first_existing(df.columns, DAY_COLUMN_CANDIDATES)
    df = _explode_outcomes_if_needed(df, outcome_col)
    df, normalized_day_col = _normalize_day_column(df, day_col)

    df = df[df[outcome_col].notna()].copy()
    df[mouse_col] = df[mouse_col].astype(str).str.strip()
    df[outcome_col] = df[outcome_col].astype(str).str.strip().str.upper()
    df = df[df[mouse_col] != ""]

    return df, mouse_col, outcome_col


def main():
    st.set_page_config(page_title="Basic Results Analysis", layout="wide")
    st.title("Basic Results Analysis")
    st.caption("Initial Streamlit analysis: result distribution by mouse and day range.")

    st.subheader("Data Source")
    uploaded_file = st.file_uploader("Choose a TXT/CSV file", type=["txt", "csv"])
    use_uploaded = uploaded_file is not None
    source_label = "uploaded file" if use_uploaded else f"default path ({DEFAULT_DATA_PATH})"

    try:
        if use_uploaded:
            data, mouse_col, outcome_col = load_and_prepare(uploaded_file)
        else:
            default_path = Path(DEFAULT_DATA_PATH)
            if not default_path.exists():
                st.warning(
                    "Default file was not found. Upload a file to continue.\n\n"
                    f"Missing path: `{DEFAULT_DATA_PATH}`"
                )
                st.stop()
            data, mouse_col, outcome_col = load_and_prepare(default_path)
    except Exception as exc:
        st.error(f"Failed loading data from {source_label}: {exc}")
        st.stop()

    st.success(f"Loaded {len(data):,} rows from {source_label}.")
    st.write(
        f"Detected columns - Mouse: `{mouse_col}` | Outcome: `{outcome_col}` | Day: `analysis_day`"
    )

    valid_days = data["analysis_day"].dropna()
    if valid_days.empty:
        st.error("No valid day values found after parsing.")
        st.stop()

    st.subheader("Filters")
    unique_days = sorted(valid_days.unique().tolist())
    if not unique_days:
        st.error("No valid days found for filtering.")
        st.stop()

    label_map_df = (
        data[["analysis_day", "analysis_date_label"]]
        .dropna(subset=["analysis_day"])
        .drop_duplicates(subset=["analysis_day"])
        .copy()
    )
    day_to_label = dict(
        zip(
            label_map_df["analysis_day"].tolist(),
            label_map_df["analysis_date_label"].astype(str).tolist(),
        )
    )
    day_labels = [day_to_label.get(d, str(d)) for d in unique_days]

    st.write(f"Available days: `{day_labels[0]}` to `{day_labels[-1]}`")

    col_from, col_to = st.columns(2)
    with col_from:
        start_day = st.selectbox("From day", options=unique_days, format_func=lambda d: day_to_label[d], index=0)
    with col_to:
        start_idx = unique_days.index(start_day)
        end_day = st.selectbox(
            "To day",
            options=unique_days[start_idx:],
            format_func=lambda d: day_to_label[d],
            index=len(unique_days[start_idx:]) - 1,
        )

    day_start, day_end = start_day, end_day
    start_label = day_to_label.get(day_start, str(day_start))
    end_label = day_to_label.get(day_end, str(day_end))

    filtered = data[(data["analysis_day"] >= day_start) & (data["analysis_day"] <= day_end)].copy()
    if filtered.empty:
        st.warning("No rows in selected day range.")
        st.stop()

    all_mice = sorted(filtered[mouse_col].dropna().astype(str).unique().tolist())
    if not all_mice:
        st.warning("No mice found in selected day range.")
        st.stop()

    range_key = f"{day_start}_{day_end}"
    selected_mice = st.multiselect(
        "Choose mice to display",
        options=all_mice,
        default=all_mice,
        key=f"mice_in_range_{range_key}",
    )
    if not selected_mice:
        st.warning("Please select at least one mouse.")
        st.stop()

    selected_mice = [str(m).strip() for m in selected_mice]
    plot_df = filtered[filtered[mouse_col].astype(str).str.strip().isin(selected_mice)].copy()
    if plot_df.empty:
        st.warning("No rows found for the selected mice in the selected date range.")
        st.stop()

    st.subheader("Distribution by Mouse")
    by_mouse = (
        plot_df.groupby([mouse_col, outcome_col], dropna=False)
        .size()
        .reset_index(name="Count")
    )
    by_mouse[mouse_col] = by_mouse[mouse_col].astype(str).str.strip()
    by_mouse["mouse_label"] = pd.Categorical(by_mouse[mouse_col], categories=selected_mice, ordered=True)

    fig_mouse = px.bar(
        by_mouse,
        x="mouse_label",
        y="Count",
        color=outcome_col,
        barmode="stack",
        title=f"Selected mice ({len(selected_mice)}) - {start_label} to {end_label}",
        category_orders={"mouse_label": selected_mice},
    )
    fig_mouse.update_layout(xaxis_title="Mouse")
    fig_mouse.update_xaxes(type="category")
    st.plotly_chart(fig_mouse, use_container_width=True)

    st.subheader("Preview")
    st.dataframe(plot_df.head(200), use_container_width=True)


if __name__ == "__main__":
    main()
