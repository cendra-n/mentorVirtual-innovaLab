CREATE TABLE IF NOT EXISTS enrollment_enrollment (
    id SERIAL PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses_course(id) ON DELETE CASCADE,
    CONSTRAINT unique_student_course UNIQUE(student_id, course_id)
);