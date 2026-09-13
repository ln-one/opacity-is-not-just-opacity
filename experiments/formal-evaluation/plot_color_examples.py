"""Single-column white-canvas illustration; retain both canvases in source data."""
from pathlib import Path
import csv,json,sys,hashlib
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'vendor-python'))
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from figure_checks import require_matplotlib_panel_alignment
from numerical import decode,encode,render
O=P/'figures'
ALPHAS=[.6,.9,1,1.1,1.4,2]
BACKGROUNDS=['#FFFFFF','#181818']

def build_data():
 upstream=json.loads((P.parents[1]/'upstream.json').read_text())['vibrant'];sources=list(upstream.values())
 f=decode(np.array([[int(h[k:k+2],16)/255 for k in (1,3,5)] for h in sources]))
 rows=[];colors={}
 for h in BACKGROUNDS:
  b=decode(np.array([int(h[k:k+2],16)/255 for k in (1,3,5)]))
  for a in ALPHAS:
   out,clipped=render(f,b,str(a));encoded=encode(out);q=np.rint(encoded*255).astype(np.uint8)
   if a==1:assert ['#'+''.join(f'{v:02X}' for v in c) for c in q]==sources
   colors[h,a]=q/255.
   for i,(name,source) in enumerate(upstream.items()):
    rows.append(dict(background=h,alpha=a,source_index=i+1,source_name=name,source_hex=source,output_hex='#'+''.join(f'{v:02X}' for v in q[i]),clipped=bool(clipped[i])))
 with (O/'color-examples-source.csv').open('w') as fh:
  w=csv.DictWriter(fh,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
 return colors

def draw(theme,colors):
 dark=theme=='dark';face='#181A1B' if dark else '#FFFFFF';fg='#E8E6E3' if dark else '#222222'
 mpl.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Arial','DejaVu Sans'],'font.size':8,'axes.labelsize':8,'xtick.labelsize':8,'ytick.labelsize':8,'svg.fonttype':'none','pdf.fonttype':42,'figure.facecolor':face,'text.color':fg,'axes.labelcolor':fg,'savefig.facecolor':face})
 fig,ax=plt.subplots(figsize=(89/25.4,77/25.4))
 fig.subplots_adjust(left=.14,right=.98,bottom=.04,top=.85)
 for ax,bg in [(ax,'#FFFFFF')]:
  ax.set_facecolor(bg);ax.set_xlim(0,7);ax.set_ylim(6,0);ax.set_xticks([]);ax.set_yticks([])
  for sp in ax.spines.values():sp.set_visible(False)
  ax.set_title('Light canvas',loc='left',pad=11,fontsize=9)
  for j,a in enumerate(ALPHAS):
   for i,c in enumerate(colors[bg,a]):
    ax.add_patch(Rectangle((i+.16,j+.20),.68,.60,facecolor=c,edgecolor='none'))
   ax.annotate(f'{a:.1f}',(0,j+.5),xycoords='data',xytext=(-11,0),textcoords='offset points',ha='right',va='center',fontsize=8,weight='bold' if a==1 else 'normal')
 fig.text(.096,.918,'α',fontsize=9,ha='right',va='center')
 fig.canvas.draw();base=O/f'color-examples-{theme}'
 require_matplotlib_panel_alignment(fig,json_out=str(base)+'.alignment.json',strict=True)
 fig.savefig(str(base)+'.pdf');fig.savefig(str(base)+'.svg',facecolor='none');fig.savefig(str(base)+'.png',dpi=300);plt.close(fig)

if __name__=='__main__':
 colors=build_data()
 for theme in ['light','dark']:draw(theme,colors)
