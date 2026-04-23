-- ============================================================
-- DFW RATE BY COURSE
-- Identifies barrier courses with high D/F/Withdraw rates
-- ============================================================
SELECT
    e.code_module,
    e.code_presentation,
    COUNT(*) AS total_enrolled,
    SUM(CASE WHEN e.final_result IN ('Fail', 'Withdrawn') THEN 1 ELSE 0 END) AS dfw_count,
    ROUND(SUM(CASE WHEN e.final_result IN ('Fail', 'Withdrawn') THEN 1.0 ELSE 0 END)
        / COUNT(*) * 100, 1) AS dfw_rate_pct,
    AVG(e.grade_points) AS avg_gpa
FROM fact_enrollment e
GROUP BY e.code_module, e.code_presentation
HAVING COUNT(*) >= 20
ORDER BY dfw_rate_pct DESC;
