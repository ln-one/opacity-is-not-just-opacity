"""Dependency-free layout checks for this repository's Matplotlib figures."""
import json
import math
from pathlib import Path


def require_matplotlib_panel_alignment(fig, json_out, exclude_axes=(),
                                      row_groups=None, column_groups=None,
                                      require_panel_labels=False, strict=True):
    """Check panel bounds and alignment without changing the rendered figure."""
    fig.canvas.draw()
    axes = [a for a in fig.axes if a not in exclude_axes]
    boxes = {chr(97+i): tuple(a.get_position().bounds) for i,a in enumerate(axes)}
    errors = []
    for key, (x,y,w,h) in boxes.items():
        if not all(math.isfinite(v) for v in (x,y,w,h)) or min(w,h)<=0:
            errors.append(f'{key}: invalid panel bounds')
        elif min(x,y)<-0.002 or x+w>1.002 or y+h>1.002:
            errors.append(f'{key}: panel outside figure')
    # Infer rows/columns only for panels sharing their center coordinates.
    def groups(coord):
        result=[]
        for key,b in boxes.items():
            center=b[coord]+b[coord+2]/2
            for group in result:
                a=boxes[group[0]]
                if abs(center-a[coord]-a[coord+2]/2)<0.015:
                    group.append(key);break
            else: result.append([key])
        return result
    for kind, collection, dims in [('row',row_groups or groups(1),(1,3)),
                                   ('column',column_groups or groups(0),(0,2))]:
        for group in collection:
            for dim in dims:
                vals=[boxes[key][dim] for key in group]
                if max(vals)-min(vals)>0.005:
                    errors.append(f'{kind} {group}: misaligned bounds')
    if require_panel_labels:
        texts=[t.get_text().strip() for t in fig.findobj() if hasattr(t,'get_text')]
        for key in boxes:
            if not any(t==key or t.startswith(key+' ') or t.startswith(key+'\n') for t in texts):
                errors.append(f'{key}: missing panel label')
    report={'checker':'repository figure bounds and alignment','panels':boxes,'errors':errors}
    Path(json_out).write_text(json.dumps(report,indent=2)+'\n')
    if strict and errors: raise ValueError('; '.join(errors))
    return report
