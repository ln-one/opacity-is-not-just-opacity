"""All 81 measured coefficients: median and block-mean variability, no smoothing."""
from pathlib import Path
import sys,json,csv
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'vendor-python'))
sys.path.insert(0,str(Path.home()/'.codex/skills/nature-figure/scripts'))
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from audit_panel_alignment import require_matplotlib_panel_alignment
O=P/'figures';BROWSERS=['chrome','firefox','webkit'];COLOR='#009988'
def load():
 data={b:json.loads((P/'results'/f'timing-sweep-{b}.json').read_text()) for b in BROWSERS}
 rows=[]
 for b,d in data.items():
  assert len(d['stats'])==81 and np.allclose(d['alphas'],np.arange(81)/40)
  for x in d['stats']:
   assert x['p10Ms']<=x['medianMs']<=x['p90Ms']
   rows.append({'browser':b,**x})
 with (O/'timing-sweep-source.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
 return data

def draw(theme,data):
 dark=theme=='dark';bg='#181A1B' if dark else '#FFFFFF';fg='#E8E6E3' if dark else '#222222';neutral='#AAB1B7' if dark else '#7A838A';grid='#3C4246' if dark else '#E1E4E6'
 mpl.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Arial','DejaVu Sans'],'font.size':8,'axes.labelsize':8,'xtick.labelsize':7,'ytick.labelsize':7,'legend.fontsize':8,'legend.frameon':False,'svg.fonttype':'none','pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':.65,'axes.edgecolor':neutral,'axes.labelcolor':fg,'text.color':fg,'xtick.color':fg,'ytick.color':fg,'figure.facecolor':bg,'axes.facecolor':'none','savefig.facecolor':bg})
 fig,axs=plt.subplots(1,3,figsize=(183/25.4,70/25.4),gridspec_kw={'wspace':.24})
 fig.subplots_adjust(left=.085,right=.985,bottom=.20,top=.75)
 upper=max(x['p90Ms'] for d in data.values() for x in d['stats']);top=np.ceil(upper*1.05/.1)*.1
 for i,(ax,b,name) in enumerate(zip(axs,BROWSERS,['Chrome','Firefox','WebKit'])):
  d=data[b]['stats'];a=np.array([x['alpha'] for x in d]);median=np.array([x['medianMs'] for x in d]);lo=np.array([x['p10Ms'] for x in d]);hi=np.array([x['p90Ms'] for x in d])
  ax.fill_between(a,lo,hi,color=COLOR,alpha=.18,lw=0,zorder=2)
  ax.plot(a,median,color=COLOR,lw=1.2,marker='o',markevery=20,ms=2.4,mfc=bg,mew=.75,zorder=3)
  ax.axvline(1,color=neutral,ls=(0,(2,3)),lw=.75,zorder=1)
  ax.set_xlim(0,2);ax.set_xticks([0,.5,1,1.5,2]);ax.set_ylim(0,top);ax.set_xlabel('Coefficient α',labelpad=5)
  if i==0:ax.set_ylabel('Per-frame time (ms)',labelpad=5)
  ax.grid(axis='y',color=grid,lw=.55);ax.set_axisbelow(True)
  ax.annotate('abc'[i],(0,1),xycoords='axes fraction',xytext=(0,10),textcoords='offset points',weight='bold',fontsize=9,ha='left',va='bottom')
  ax.set_title(name,loc='left',x=.09,pad=10,fontsize=9)
 handles=[Line2D([],[],color=COLOR,lw=1.2,label='Median'),Patch(facecolor=COLOR,alpha=.18,label='10th–90th percentile')]
 fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.53,.99),ncol=2,handlelength=2.4,columnspacing=2)
 fig.canvas.draw();base=O/f'timing-sweep-{theme}'
 require_matplotlib_panel_alignment(fig,json_out=str(base)+'.alignment.json',require_panel_labels=True,strict=True)
 fig.savefig(str(base)+'.pdf');fig.savefig(str(base)+'.svg',facecolor='none');fig.savefig(str(base)+'.png',dpi=600);plt.close(fig)
if __name__=='__main__':
 data=load()
 for theme in ['light','dark']:draw(theme,data)
