import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st
from typing import Dict, Any, List
from frontend.config import EMOTION_COLORS


def _display_plotly(fig):
    """Safely displays Plotly chart responsively across Streamlit versions."""
    try:
        st.plotly_chart(fig, width="stretch")
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)


def render_emotion_pie_chart(distribution: Dict[str, int]):
    """Renders Plotly Pie Chart of Emotion Breakdown."""
    if not distribution:
        st.info("No emotion data available yet. Start journaling to unlock charts!")
        return

    labels = [k.capitalize() for k in distribution.keys()]
    values = list(distribution.values())
    colors = [EMOTION_COLORS.get(k.lower(), "#64748b") for k in distribution.keys()]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0,  # Pure Pie Chart
                marker=dict(colors=colors, line=dict(color="#ffffff", width=2)),
                hoverinfo="label+percent+value",
                textinfo="label+percent",
                textfont=dict(size=13, family="sans-serif")
            )
        ]
    )

    fig.update_layout(
        title=dict(text="<b>🎭 Emotion Distribution (Pie Chart)</b>", font=dict(size=17, color="#1e293b")),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.22, xanchor="center", x=0.5),
        margin=dict(l=20, r=20, t=50, b=30),
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    _display_plotly(fig)


def render_average_sentiment_gauge(avg_sentiment: float, sentiment_label: str, positive_pct: float = 0.0, negative_pct: float = 0.0):
    """Renders Plotly Gauge Indicator Chart for Average Sentiment."""
    # Determine bar color based on score
    if avg_sentiment >= 0.05:
        bar_color = "#10b981"  # Emerald green
    elif avg_sentiment <= -0.05:
        bar_color = "#ef4444"  # Rose red
    else:
        bar_color = "#64748b"  # Slate neutral

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=avg_sentiment,
            domain=dict(x=[0, 1], y=[0, 1]),
            title=dict(
                text=f"<b>Average Sentiment Score</b><br><span style='font-size:0.85em;color:#64748b;'>Classification: <b>{sentiment_label}</b></span>",
                font=dict(size=16, color="#1e293b")
            ),
            delta=dict(
                reference=0.0,
                increasing=dict(color="#10b981"),
                decreasing=dict(color="#ef4444"),
                prefix="Compound: "
            ),
            gauge=dict(
                axis=dict(range=[-1.0, 1.0], tickwidth=1, tickcolor="#94a3b8", dtick=0.5),
                bar=dict(color=bar_color, thickness=0.3),
                bgcolor="white",
                borderwidth=2,
                bordercolor="#e2e8f0",
                steps=[
                    dict(range=[-1.0, -0.05], color="rgba(239, 68, 68, 0.15)"),
                    dict(range=[-0.05, 0.05], color="rgba(148, 163, 184, 0.15)"),
                    dict(range=[0.05, 1.0], color="rgba(16, 185, 129, 0.15)")
                ],
                threshold=dict(
                    line=dict(color="#4f46e5", width=3),
                    thickness=0.75,
                    value=avg_sentiment
                )
            )
        )
    )

    fig.update_layout(
        margin=dict(l=25, r=25, t=60, b=25),
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    _display_plotly(fig)


def render_emotion_donut_chart(distribution: Dict[str, int]):
    """Renders Plotly Donut Chart of Emotion Breakdown."""
    if not distribution:
        st.info("No emotion data available yet. Start journaling to unlock charts!")
        return

    labels = [k.capitalize() for k in distribution.keys()]
    values = list(distribution.values())
    colors = [EMOTION_COLORS.get(k.lower(), "#64748b") for k in distribution.keys()]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.55,
                marker=dict(colors=colors, line=dict(color="#ffffff", width=2)),
                hoverinfo="label+percent+value",
                textinfo="label+percent",
                textfont=dict(size=13, family="sans-serif")
            )
        ]
    )

    fig.update_layout(
        title=dict(text="<b>Overall Emotion Distribution</b>", font=dict(size=17, color="#1e293b")),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        margin=dict(l=20, r=20, t=50, b=30),
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    _display_plotly(fig)



def render_sentiment_line_chart(timeline: List[Dict[str, Any]]):
    """Renders Plotly Line Chart for Sentiment Progression Over Time."""
    if not timeline or len(timeline) < 1:
        st.info("Record at least one journal entry to view your sentiment trajectory.")
        return

    df = pd.DataFrame(timeline)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    # Rolling average if more than 3 entries
    if len(df) >= 3:
        df["rolling_avg"] = df["compound"].rolling(window=3, min_periods=1).mean()

    fig = go.Figure()

    # Base line
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["compound"],
            mode="lines+markers",
            name="Daily Sentiment",
            line=dict(color="#6366f1", width=2.5),
            marker=dict(size=9, color="#4f46e5", line=dict(color="#ffffff", width=1.5)),
            hovertemplate="<b>%{x|%b %d, %Y}</b><br>Score: %{y:.2f}<br>Emotion: %{customdata[0]}<br>Title: %{customdata[1]}<extra></extra>",
            customdata=df[["primary_emotion", "title"]]
        )
    )

    # Rolling Trend Line if present
    if "rolling_avg" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df["date"],
                y=df["rolling_avg"],
                mode="lines",
                name="3-Day Trend",
                line=dict(color="#ec4899", width=2, dash="dot"),
                hoverinfo="skip"
            )
        )

    # Neutral Reference Line
    fig.add_hline(y=0.0, line_dash="dash", line_color="#94a3b8", annotation_text="Neutral (0.0)")

    fig.update_layout(
        title=dict(text="<b>Sentiment Trajectory Over Time</b>", font=dict(size=17, color="#1e293b")),
        xaxis=dict(title="Date", showgrid=True, gridcolor="#f1f5f9"),
        yaxis=dict(title="VADER Compound Score (-1 to +1)", range=[-1.05, 1.05], showgrid=True, gridcolor="#f1f5f9"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        margin=dict(l=20, r=20, t=50, b=30),
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    _display_plotly(fig)


def render_emotion_radar_chart(radar_data: Dict[str, float]):
    """Renders Plotly Polar / Radar Chart for Emotion Intensity Dimensions."""
    if not radar_data:
        return

    categories = [k.capitalize() for k in radar_data.keys()]
    values = list(radar_data.values())

    # Close the polygon loop
    categories.append(categories[0])
    values.append(values[0])

    fig = go.Figure(
        data=go.Scatterpolar(
            r=values,
            theta=categories,
            fill="toself",
            name="Intensity",
            line=dict(color="#8b5cf6", width=2),
            fillcolor="rgba(139, 92, 246, 0.25)"
        )
    )

    fig.update_layout(
        title=dict(text="<b>Emotional Intensity Balance (DistilBERT)</b>", font=dict(size=17, color="#1e293b")),
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1.0], gridcolor="#e2e8f0"),
            angularaxis=dict(gridcolor="#e2e8f0")
        ),
        showlegend=False,
        margin=dict(l=20, r=20, t=50, b=30),
        height=380,
        paper_bgcolor="rgba(0,0,0,0)"
    )

    _display_plotly(fig)


def render_keywords_bar_chart(keywords: List[Dict[str, Any]]):
    """Renders Horizontal Bar Chart for Top Trigger Keywords."""
    if not keywords:
        st.info("Write a few journal entries to see your top recurring themes and keywords.")
        return

    df = pd.DataFrame(keywords)
    df = df.sort_values("count", ascending=True)

    fig = go.Figure(
        go.Bar(
            x=df["count"],
            y=df["keyword"],
            orientation="h",
            marker=dict(
                color=df["count"],
                colorscale="Viridis",
                line=dict(color="#ffffff", width=1)
            ),
            hovertemplate="Keyword: <b>%{y}</b><br>Occurrences: %{x}<extra></extra>"
        )
    )

    fig.update_layout(
        title=dict(text="<b>Top Recurring Mood Keywords & Triggers</b>", font=dict(size=17, color="#1e293b")),
        xaxis=dict(title="Frequency", showgrid=True, gridcolor="#f1f5f9"),
        yaxis=dict(title="Keywords"),
        margin=dict(l=20, r=20, t=50, b=30),
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    _display_plotly(fig)


def render_weekly_bar_chart(weekly_data: Dict[str, int]):
    """Renders Day of Week Distribution."""
    if not weekly_data or sum(weekly_data.values()) == 0:
        return

    days = list(weekly_data.keys())
    counts = list(weekly_data.values())

    fig = go.Figure(
        go.Bar(
            x=days,
            y=counts,
            marker_color="#06b6d4",
            marker_line=dict(color="#ffffff", width=1)
        )
    )

    fig.update_layout(
        title=dict(text="<b>Journaling Activity by Day of the Week</b>", font=dict(size=17, color="#1e293b")),
        xaxis=dict(title="Day"),
        yaxis=dict(title="Entries Logged", dtick=1),
        margin=dict(l=20, r=20, t=50, b=30),
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    _display_plotly(fig)


def render_emotion_probability_bars(all_emotions: List[Dict[str, Any]]):
    """Renders horizontal probability breakdown for live analysis."""
    if not all_emotions:
        return

    df = pd.DataFrame(all_emotions)
    df["percentage"] = df["score"] * 100
    df = df.sort_values("score", ascending=True)

    colors = [EMOTION_COLORS.get(e.lower(), "#64748b") for e in df["emotion"]]

    fig = go.Figure(
        go.Bar(
            x=df["percentage"],
            y=[e.capitalize() for e in df["emotion"]],
            orientation="h",
            marker=dict(color=colors),
            text=[f"{p:.1f}%" for p in df["percentage"]],
            textposition="auto"
        )
    )

    fig.update_layout(
        title=dict(text="<b>Emotion Probability Spectrum (DistilBERT)</b>", font=dict(size=15, color="#1e293b")),
        xaxis=dict(title="Confidence (%)", range=[0, 100]),
        margin=dict(l=10, r=10, t=40, b=20),
        height=280,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    _display_plotly(fig)


def render_monthly_report_chart(monthly_report: List[Dict[str, Any]]):
    """Renders Plotly Dual-Axis Monthly Report Chart (Check-ins + Average Sentiment)."""
    if not monthly_report:
        st.info("No monthly data available yet. Continue journaling to generate your monthly reports!")
        return

    df = pd.DataFrame(monthly_report)
    months = df["month_label"].tolist()
    checkins = df["total_entries"].tolist()
    sentiments = df["avg_sentiment"].tolist()
    pos_entries = df["positive_entries"].tolist()
    neg_entries = df["negative_entries"].tolist()

    fig = go.Figure()

    # Bar trace: Positive entries
    fig.add_trace(
        go.Bar(
            x=months,
            y=pos_entries,
            name="Positive Check-ins",
            marker_color="#10b981",
            hovertemplate="Month: <b>%{x}</b><br>Positive Entries: %{y}<extra></extra>"
        )
    )

    # Bar trace: Negative entries
    fig.add_trace(
        go.Bar(
            x=months,
            y=neg_entries,
            name="Negative Check-ins",
            marker_color="#ef4444",
            hovertemplate="Month: <b>%{x}</b><br>Negative Entries: %{y}<extra></extra>"
        )
    )

    # Line trace on secondary Y-axis: Average Sentiment
    fig.add_trace(
        go.Scatter(
            x=months,
            y=sentiments,
            name="Avg Sentiment Score",
            yaxis="y2",
            mode="lines+markers",
            line=dict(color="#6366f1", width=3),
            marker=dict(size=10, color="#4338ca", symbol="diamond"),
            hovertemplate="Month: <b>%{x}</b><br>Avg Sentiment: <b>%{y:.2f}</b><extra></extra>"
        )
    )

    fig.update_layout(
        title=dict(text="<b>📅 Monthly Report: Check-in Activity & Sentiment</b>", font=dict(size=17, color="#1e293b")),
        barmode="stack",
        xaxis=dict(title="Month"),
        yaxis=dict(title="Total Check-ins", dtick=1, showgrid=True, gridcolor="#f1f5f9"),
        yaxis2=dict(
            title="Avg Sentiment Compound",
            overlaying="y",
            side="right",
            range=[-1.05, 1.05],
            showgrid=False
        ),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        margin=dict(l=20, r=20, t=50, b=30),
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    _display_plotly(fig)

