"""Generate a compact author-facing report from stored measurements."""
import csv
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
R=HERE/'results'


def main():
    full=[json.loads(p.read_text()) for p in sorted(R.glob('full-*.json'))]
    assert len(full)==16
    cfg=json.loads((HERE/'protocol.json').read_text())
    checksum=hashlib.sha256((HERE/'protocol.json').read_bytes()).hexdigest()
    codehash=hashlib.sha256((HERE/'numerical.py').read_bytes()).hexdigest()
    allnum=full+[json.loads(p.read_text()) for p in R.glob('sweep-*.json')]+[json.loads((R/'stress.json').read_text())]
    for item in allnum:
        assert item['protocol_sha256']==checksum and item['script_sha256']==codehash
        for s in item['results'].values():
            assert s['n']==s['improved']+s['unchanged']+s['worsened']==sum(s['gain_histogram'])
    rows=[]
    for item in allnum:
        for m,s in item['results'].items():
            rows.append(dict(suite=item['suite'],background=item.get('background','regular RGB grid'),method=m,
                **{k:s[k] for k in ['n','improved','unchanged','worsened','clipped','gained3','lost3','gained45','lost45','mean_gain','min_gain','max_gain','background_distance_violations']}))
    with (R/'summary.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    total=sum(r['n'] for r in rows)
    lines=['# 大规模实验：首轮结果','',
        '本报告由已保存的测量结果生成。协议在本轮运行前固定，设计受此前 pilot 启发；不是预注册研究。尚未据此修改论文。','',
        '## 覆盖范围','',
        f'- 颜色输出计算共 **{total:,} 次**：完整 8 位 RGB × 16 画布 × 7 配置；65³ 源颜色 × 16 画布 × 81 系数；17³ 源颜色 × 33³ 背景 × 7 配置。',
        '- 系数扫描覆盖 0–2，步长 0.025。完整色域与压力测试的配置为原色、1.05、1.1、1.2、1.4、difference、exclusion。',
        '- 原色和所有混合模式在相同线性 sRGB 空间计算；浏览器原生 Canvas2D 的编码 sRGB 结果另行验证。',
        '- 16 种画布是固定的合成亮暗及轻微带色样例；压力测试使用规则色域网格。二者都不是网站使用频率样本。','',
        '## 固定画布上的完整颜色覆盖','',
        '| 配置 | 对比度提高 (%) | 下降 (%) | 平均对比度差值 |',
        '|---|---:|---:|---:|']
    for m in cfg['methods']:
        ss=[f['results'][m] for f in full];n=sum(s['n'] for s in ss)
        lines.append(f"| {m} | {100*sum(s['improved'] for s in ss)/n:.4f} | {100*sum(s['worsened'] for s in ss)/n:.4f} | {sum(s['sum_gain'] for s in ss)/n:.6f} |")
    lines+=['','每个配置覆盖 268,435,456 个源颜色—画布组合。提高/下降按绝对对比度差值 1e-10 的容差统计；均值为该枚举集合的描述统计。',
        '', '### α = 1.1 的背景分解','', '| 画布 | 下降 (%) | 最小对比度差值 |','|---|---:|---:|']
    for f in full:
        s=f['results']['1.1'];lines.append(f"| {f['background']} | {s['worsened_pct']:.4f} | {s['min_gain']:.6f} |")
    lines+=['','黑、白画布上未发现对比度下降；其余画布存在下降案例。整体高提高比例不能替代这些背景差异。各组最差案例的源颜色、背景、输出及前后对比度均保存在原始 JSON 中。',
        '', '## 广泛背景压力测试','', '| 配置 | 提高 (%) | 下降 (%) | 平均差值 |','|---|---:|---:|---:|']
    stress=json.loads((R/'stress.json').read_text())
    for m,s in stress['results'].items():lines.append(f"| {m} | {s['improved_pct']:.4f} | {s['worsened_pct']:.4f} | {s['mean_gain']:.6f} |")
    lines+=['','每个配置包含 176,558,481 个前景—背景组合。逐通道截断后的背景 RGB 距离不减检查，在所有 α≥1 的被检验组合中均未发现违反；亮度对比度下降则确实存在。',
        '', '## 对象间区分','',
        '使用 Colour Science 0.4.7 的 CIEDE2000。已通过一个公开标准校验对（ΔE00≈2.0425）；源色对去除完全相同者。随机色对采用固定种子 20260913，共 65,536 对，在 16 画布上配对比较。','',
        '| 源色对 | 系数 | 色差下降 / 总数 | 8 位颜色重合 | 最小后/前色差比 |','|---|---:|---:|---:|---:|']
    pairs=json.loads((R/'pairs.json').read_text())
    for group in ['Tol Vibrant','uniform 8-bit random pairs']:
        for m in ['1.05','1.1','1.2','1.4']:
            ss=[s for s in pairs['results'] if s['group']==group and s['method']==m]
            lines.append(f"| {group} | {m} | {sum(s['shrunk'] for s in ss):,} / {sum(s['n'] for s in ss):,} | {sum(s['mergers'] for s in ss):,} | {min(s['min_ratio'] for s in ss):.6f} |")
    lines+=['','色差与背景对比度分别评估；量化重合按 sRGB 编码后的 8 位四舍六入五成双计算。CIEDE2000 是颜色距离指标，此处没有用户识别实验，也没有灰度区分实验。',
        '', '## 浏览器与计时','',
        '300 个 Lucide 图标按文件路径 SHA-256 排序选取，固定包版本与文件校验值。三个尺寸为 16、24、48 px；所有非零覆盖像素均与 CPU 参考值比较，包括抗锯齿边缘。','',
        '| 浏览器 | 图标显示实例 | 最大通道误差 | 超出 1/255 容差的通道数 |','|---|---:|---:|---:|']
    browsers=[]
    for name in ['chrome','firefox','webkit']:
        p=R/f'browser-{name}.json'
        if not p.exists():continue
        d=json.loads(p.read_text())
        if 'evaluation' not in d:continue
        assert d['protocol_sha256']==checksum
        assert d['browser_js_sha256']==hashlib.sha256((HERE/'browser.js').read_bytes()).hexdigest()
        assert d['timing_protocol_sha256']==hashlib.sha256((HERE/'timing-protocol-v3.json').read_bytes()).hexdigest()
        assert d['timing']['alphas']==[0.6,0.9,1,1.1,1.4]
        e=d['evaluation'];browsers.append(d)
        lines.append(f"| {name} | {sum(r['icons'] for r in e['rows']):,} | {e['maxError']}/255 | {e['violations']} |")
    lines+=['','计时使用同一 WebGL shader，固定图标与分辨率、轮换背景，交错测试五个系数。每帧读取一个像素强制完成输出并校验交替背景，记录 25 组、每组 20 帧；预热 50 帧。表中为组均值的中位数（毫秒/帧）。','',
        '| 浏览器 | α=.6 | α=.9 | α=1 | α=1.1 | α=1.4 |','|---|---:|---:|---:|---:|---:|']
    for d in browsers:
        t=d['timing']['stats'];lines.append('| '+d['browser_name']+' | '+' | '.join(f"{t[a]['medianMs']:.4f}" for a in ['0.6','0.9','1','1.1','1.4'])+' |')
    lines+=['','这些时间测量当前原型的完整绘制提交与驱动同步，不能解释成原生浏览器修改前后的开销，也不证明系数间完全等时。原型将边缘覆盖率与扩展系数分开处理；读取的是应用自己管理的画布背景，不是任意 DOM 后方的像素。',
        '', '## 复现与检查','',
        '- `protocol.json`：固定配置及评测口径。',
        '- `numerical.py`：分块枚举、直方图、阈值变化及最差案例。',
        '- `pairs.py`：CIEDE2000 与量化重合。',
        '- `browser.js` / `browser_driver.py`：同一 shader 的像素检查与计时。',
        '- `results/verification.json`：独立标量公式、边界与分块一致性检查。',
        '- `results/summary.csv`：数值统计汇总；完整分布与极值在各 JSON 中。',
        '', '执行结果与术语：计算案例数不等于独立观察者样本；图标及背景的各次变换另计为显示实例。对比度阈值只作诊断，不构成整张图或页面的 WCAG 合规结论。']
    (HERE/'report.zh.md').write_text('\n'.join(lines)+'\n')
    print('report written; evaluations',total,'browser suites',len(browsers))


if __name__=='__main__':main()
