import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_allocation_heatmap(df: pd.DataFrame, title: str = "人員配置状況"):
    """配置状況のヒートマップを作成"""
    
    processes = df.columns[1:]
    locations = df['拠点'].tolist()
    values = df[processes].values
    
    fig = go.Figure(data=go.Heatmap(
        z=values,
        x=processes,
        y=locations,
        colorscale='YlOrRd',
        text=values,
        texttemplate='%{text}名',
        textfont={"size": 12},
        hoverongaps=False
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="工程",
        yaxis_title="拠点",
        height=400
    )
    
    return fig

def create_allocation_comparison(df_before: pd.DataFrame, df_after: pd.DataFrame):
    """配置変更前後の比較ビューを作成"""
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('現在の配置', '変更後の配置（案）'),
        horizontal_spacing=0.1
    )
    
    processes = df_before.columns[1:]
    locations = df_before['拠点'].tolist()
    
    fig.add_trace(
        go.Heatmap(
            z=df_before[processes].values,
            x=processes,
            y=locations,
            colorscale='YlOrRd',
            text=df_before[processes].values,
            texttemplate='%{text}',
            showscale=False
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Heatmap(
            z=df_after[processes].values,
            x=processes,
            y=locations,
            colorscale='YlOrRd',
            text=df_after[processes].values,
            texttemplate='%{text}',
            showscale=True
        ),
        row=1, col=2
    )
    
    diff = df_after[processes].values - df_before[processes].values
    diff_mask = diff != 0
    
    for i in range(len(locations)):
        for j in range(len(processes)):
            if diff_mask[i, j]:
                fig.add_annotation(
                    x=processes[j],
                    y=locations[i],
                    text=f"<b>{'+' if diff[i, j] > 0 else ''}{diff[i, j]}</b>",
                    showarrow=False,
                    xref="x2",
                    yref="y2",
                    font=dict(color="blue", size=14),
                    bgcolor="rgba(255,255,255,0.8)"
                )
    
    fig.update_layout(
        title="配置変更シミュレーション",
        height=500,
        showlegend=False
    )
    
    return fig

def create_flow_diagram(locations: list, transfers: list):
    """拠点間の人員移動フロー図を作成"""
    
    node_x = []
    node_y = []
    node_text = []
    
    for i, loc in enumerate(locations):
        angle = 2 * 3.14159 * i / len(locations)
        x = 0.5 + 0.4 * np.cos(angle)
        y = 0.5 + 0.4 * np.sin(angle)
        node_x.append(x)
        node_y.append(y)
        node_text.append(loc)
    
    edge_x = []
    edge_y = []
    
    for transfer in transfers:
        from_idx = locations.index(transfer['from'])
        to_idx = locations.index(transfer['to'])
        
        edge_x.extend([node_x[from_idx], node_x[to_idx], None])
        edge_y.extend([node_y[from_idx], node_y[to_idx], None])
    
    fig = go.Figure()
    
    for transfer in transfers:
        from_idx = locations.index(transfer['from'])
        to_idx = locations.index(transfer['to'])
        
        fig.add_trace(go.Scatter(
            x=[node_x[from_idx], node_x[to_idx]],
            y=[node_y[from_idx], node_y[to_idx]],
            mode='lines+text',
            line=dict(width=2, color='lightblue'),
            text=[None, f"{transfer['count']}名"],
            textposition="middle center",
            showlegend=False
        ))
    
    fig.add_trace(go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="bottom center",
        marker=dict(size=30, color='lightcoral'),
        showlegend=False
    ))
    
    fig.update_layout(
        title="人員移動フロー",
        showlegend=False,
        hovermode='closest',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=400
    )
    
    return fig