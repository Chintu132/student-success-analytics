SELECT
    term,
    COUNT(DISTINCT student_id) AS student_count
FROM fact_enrollment
GROUP BY term
ORDER BY term;