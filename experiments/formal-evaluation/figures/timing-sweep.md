# Full coefficient timing sweep — figure contract

Question: how does measured frame time vary across the conventional and extended coefficient intervals in the same rendering pipeline?

Three matched panels show Chrome, Firefox and WebKit. All 81 coefficients in [0,2], step 0.025, are retained. Each coefficient has 25 block means, each over 20 frames with one synchronous pixel readback per frame. Browser runs are sequential to avoid intentional GPU contention. Each round uses a seeded random permutation of all coefficients, shared across browsers. Two full warmup sweeps precede timing. The same 300 icons at 48 pixels and alternating warm/cool light/dark canvases are used for every coefficient.

Median curves with empirical 10th–90th percentile bands summarize the block means; the bands are variability ranges, not confidence intervals. Alpha 1 is marked as the conventional endpoint. Uniform shared axes and one Tol Vibrant teal encoding keep comparisons consistent; panel titles distinguish browsers. This is a matched quantitative grid answering one performance question, not three independent method claims.

Scope: CPU wall time for the unchanged WebGL draw plus synchronous one-pixel readback. This includes submission and readback costs, and does not establish the overhead of modifying a native browser compositor or pure GPU shader execution. Browser timer precision and uncontrolled machine activity are part of the measured variation. Raw block records and seeded order are retained in results/timing-sweep-*.json. Prior five-coefficient measurements remain unchanged.

Export: Python + Matplotlib, 183 x 70 mm, PDF/SVG/PNG, editable labels >=7 pt, light/dark page themes, panel-alignment and PDF collision audits. All measured data are used without smoothing or discarded outliers.

QA: light/dark previews inspected, panel alignment passed, PDF collision checks passed with no warnings, minimum text 7 pt. PDF size verified as 183 x 70 mm. Static width-expression warning is a parser artifact; TIFF omitted for this PDF/SVG/PNG draft.
