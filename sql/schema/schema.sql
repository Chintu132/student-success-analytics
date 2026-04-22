CREATE TABLE dim_student (
    student_id VARCHAR(50),
    gender VARCHAR(20),
    age_band VARCHAR(20),
    region VARCHAR(100)
);

CREATE TABLE fact_enrollment (
    student_id VARCHAR(50),
    term VARCHAR(20),
    final_grade VARCHAR(10),
    credits_attempted INT,
    credits_earned INT
);