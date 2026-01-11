import plotly.graph_objs as go
import plotly.io as pio
from components.models import PriceHistory


def get_graph(dates, prices):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates,
                             y=prices,
                             mode='lines+markers',
                             line=dict(color='#a855f7', width=3),
                             marker=dict(size=8, color='#ffffff', line=dict(color='#a855f7', width=2)),
                             name='Цена',
                             hovertemplate='%{y} ₽<extra></extra>'))

    fig.update_layout(template='plotly_dark',
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)',
                      margin=dict(l=10, r=10, b=30, t=10),
                      height=200,
                      showlegend=False,
                      autosize=True,
                      dragmode=False,
                      xaxis=dict(
                          fixedrange=True,
                          showgrid=False,
                          tickfont=dict(size=10)
                      ),
                      yaxis=dict(
                          fixedrange=True,
                          showgrid=True,
                          gridcolor='#2d3748',
                          tickformat=".1f",
                          ticksuffix=" тыс. ₽",
                          tickfont=dict(size=10)))

    config = {
        'displayModeBar': False,
        'responsive': True
    }

    return pio.to_html(fig, full_html=False, include_plotlyjs='cdn', config=config)

def get_component_graph(component_id, component_type):
    history = PriceHistory.objects.filter(component_id=component_id, component_type=component_type).order_by('date_checked')

    if not history.exists():
        return None

    dates = [h.date_checked.strftime("%d.%m") for h in history]
    prices = [float(h.price) / 1000 for h in history]
    return get_graph(dates, prices)