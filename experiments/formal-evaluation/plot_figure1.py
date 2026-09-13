"""Figure 1: alpha-dependent enhancement, failures and color mergers.
Deterministic enumeration, no CI. Main: 41 measured coefficients in [1,2]. Supplement: all 81 in [0,2]. No smoothing.
Paul Tol Vibrant: light = orange/solid/circle; dark = blue/dashed/square.
"""
from pathlib import Path
import csv,json,sys
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'vendor-python'))
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator, FuncFormatter
from figure_checks import require_matplotlib_panel_alignment

OUT=P/'figures'
COLORS={'Light canvases':'#EE7733','Dark canvases':'#0077BB'}
STYLES={'Light canvases':('-', 'o'),'Dark canvases':((0,(4,2)), 's')}

def draw(theme, full=False):
 dark=theme=='dark';bg='#181A1B' if dark else '#FFFFFF';fg='#E8E6E3' if dark else '#222222';grid='#3C4246' if dark else '#E1E4E6';neutral='#AAB1B7' if dark else '#7A838A'
 mpl.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Arial','DejaVu Sans'],'font.size':8,'axes.labelsize':8,'xtick.labelsize':7,'ytick.labelsize':7,'legend.fontsize':8,'legend.frameon':False,'svg.fonttype':'none','pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':.65,'axes.edgecolor':neutral,'axes.labelcolor':fg,'text.color':fg,'xtick.color':fg,'ytick.color':fg,'figure.facecolor':bg,'axes.facecolor':'none','savefig.facecolor':bg})
 data=list(csv.DictReader((OUT/'figure1-source.csv').open()))
 fields=['mean_contrast_gain','contrast_decreased_pct','merged_pairs_pct']
 fig,axs=plt.subplots(1,3,figsize=(183/25.4,70/25.4),gridspec_kw={'wspace':.40})
 fig.subplots_adjust(left=.075,right=.985,bottom=.19,top=.77)
 insets=[];handles=[]
 for group in COLORS:
  rows=[r for r in data if r['canvas_group']==group and (full or float(r['alpha'])>=1)];a=np.array([float(r['alpha']) for r in rows]);assert len(a)==(81 if full else 41) and np.all(np.diff(a)>0)
  ls,marker=STYLES[group]
  for k,ax in enumerate(axs):
   y=np.array([float(r[fields[k]]) for r in rows])
   line,=ax.plot(a,y,color=COLORS[group],ls=ls,marker=marker,markevery=20 if full else 10,clip_on=False,ms=2.9,mew=.7,mfc=bg,lw=1.4,label=group,zorder=3)
   if k==0:handles.append(line)
 titles=['Contrast gain','Contrast decreases','Color mergers']
 labels=['Mean contrast change','Contrast decreases (%)','Color-pair mergers (%)']
 for k,ax in enumerate(axs):
  ax.set_xlim(0 if full else 1,2);ax.set_xticks([0,.5,1,1.5,2] if full else [1,1.25,1.5,1.75,2]);ax.xaxis.set_major_formatter(FuncFormatter(lambda v,p:f'{v:g}'));ax.set_xlabel('Coefficient α',labelpad=5);ax.set_ylabel(labels[k],labelpad=5)
  ax.set_axisbelow(True);ax.grid(axis='y',color=grid,lw=.55)
  if full:ax.axvline(1,color=neutral,ls=(0,(2,3)),lw=.8,zorder=1)
  ax.annotate('abc'[k],(0,1),xycoords='axes fraction',xytext=(0,11),textcoords='offset points',weight='bold',fontsize=9,ha='left',va='bottom')
  ax.set_title(titles[k],loc='left',x=.085,pad=11,fontsize=8.3,weight='normal')
  ax.tick_params(length=3,width=.6)
  if full:
   if k==0:ax.axhline(0,color=neutral,lw=.65,zorder=1);ax.yaxis.set_major_locator(MaxNLocator(5))
   else:ax.set_ylim(0,105);ax.set_yticks([0,25,50,75,100])
  else:
   limits=[(0,8),(0,1),(0,15)];ticks=[[0,2,4,6,8],[0,.2,.4,.6,.8,1],[0,5,10,15]]
   ax.set_ylim(*limits[k]);ax.set_yticks(ticks[k]);ax.yaxis.set_major_formatter(FuncFormatter(lambda v,p:f'{v:g}'))
   assert all(max(line.get_ydata())<=limits[k][1] for line in ax.lines)
 fig.legend(handles,list(COLORS),loc='upper center',bbox_to_anchor=(.52,.98),ncol=2,handlelength=2.8,columnspacing=2.4)
 fig.canvas.draw()
 base=OUT/f"figure1-{'full-range-' if full else ''}{theme}"
 require_matplotlib_panel_alignment(fig,json_out=str(base)+'.alignment.json',exclude_axes=insets,require_panel_labels=True,strict=True)
 fig.savefig(str(base)+'.pdf');fig.savefig(str(base)+'.svg',facecolor='none');fig.savefig(str(base)+'.png',dpi=300)
 plt.close(fig)

if __name__=='__main__':
 for theme in ['light','dark']:
  draw(theme);draw(theme,full=True)
