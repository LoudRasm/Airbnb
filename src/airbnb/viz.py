"""TV1: nối các file vẽ của từng thành viên; không chứa logic vẽ của người khác."""
from . import viz_market, viz_qa, viz_spatial, viz_calendar, viz_reviews


def render_all(tables, figures, cfg, skip_llm=False):
    paths = []
    for module in [viz_market, viz_qa, viz_spatial, viz_calendar]:
        paths.extend(module.render(tables, figures, cfg))
    if not skip_llm:
        paths.extend(viz_reviews.render(tables, figures, cfg))
    return paths
