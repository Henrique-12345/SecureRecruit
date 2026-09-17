"""Seed database with fictional demo data."""

from __future__ import annotations

import hashlib
from datetime import date
from pathlib import Path

from docx import Document

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.enums import ApplicationStatus, EmploymentType, JobStatus, UserRole
from app.core.security import hash_password
from app.models.ai_analysis import AIAnalysis
from app.models.application import Application
from app.models.candidate_profile import CandidateProfile
from app.models.job import Job
from app.models.resume import Resume
from app.models.security_log import SecurityLog
from app.models.user import User


DEMO_PASSWORD = "Demo@1234"


def _write_sample_docx(path: Path, content_lines: list[str]) -> tuple[int, str]:
    document = Document()
    for line in content_lines:
        document.add_paragraph(line)
    document.save(path)
    data = path.read_bytes()
    return len(data), hashlib.sha256(data).hexdigest()


def seed() -> None:
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == "admin@example.com").first()
        if existing:
            print("Seed already applied. Skipping.")
            return

        upload_dir = Path(settings.UPLOAD_DIRECTORY)
        upload_dir.mkdir(parents=True, exist_ok=True)

        admin = User(
            name="Admin Demo",
            email="admin@example.com",
            password_hash=hash_password(DEMO_PASSWORD),
            role=UserRole.ADMIN.value,
            cpf="000.000.000-00",
            phone="(81) 90000-0000",
            birth_date=date(1990, 1, 1),
            is_active=True,
        )

        recruiters = [
            User(
                name="Recrutadora Ana Silva",
                email="ana.recruiter@example.com",
                password_hash=hash_password(DEMO_PASSWORD),
                role=UserRole.RECRUITER.value,
                cpf="111.111.111-11",
                phone="(81) 91111-1111",
                birth_date=date(1988, 5, 12),
                is_active=True,
            ),
            User(
                name="Recrutador Bruno Costa",
                email="bruno.recruiter@example.com",
                password_hash=hash_password(DEMO_PASSWORD),
                role=UserRole.RECRUITER.value,
                cpf="222.222.222-22",
                phone="(81) 92222-2222",
                birth_date=date(1985, 8, 20),
                is_active=True,
            ),
        ]

        candidates = [
            User(
                name="Candidato Carlos Mendes",
                email="carlos.candidate@example.com",
                password_hash=hash_password(DEMO_PASSWORD),
                role=UserRole.CANDIDATE.value,
                cpf="333.333.333-33",
                phone="(81) 93333-3333",
                birth_date=date(1995, 3, 15),
                is_active=True,
            ),
            User(
                name="Candidata Diana Rocha",
                email="diana.candidate@example.com",
                password_hash=hash_password(DEMO_PASSWORD),
                role=UserRole.CANDIDATE.value,
                cpf="444.444.444-44",
                phone="(81) 94444-4444",
                birth_date=date(1997, 7, 8),
                is_active=True,
            ),
            User(
                name="Candidato Eduardo Lima",
                email="eduardo.candidate@example.com",
                password_hash=hash_password(DEMO_PASSWORD),
                role=UserRole.CANDIDATE.value,
                cpf="555.555.555-55",
                phone="(81) 95555-5555",
                birth_date=date(1994, 11, 22),
                is_active=True,
            ),
        ]

        db.add(admin)
        db.add_all(recruiters)
        db.add_all(candidates)
        db.flush()

        profiles = [
            CandidateProfile(
                user_id=candidates[0].id,
                address="Rua Fictícia 100",
                city="Recife",
                state="PE",
                professional_summary="Desenvolvedor backend com foco em Python e APIs.",
                education="Bacharelado em Ciência da Computação - Universidade Demo",
                skills="Python, FastAPI, PostgreSQL, Docker, Linux",
                experience="3 anos em desenvolvimento de APIs REST",
                linkedin_url="https://linkedin.com/in/carlos-demo",
            ),
            CandidateProfile(
                user_id=candidates[1].id,
                address="Av. Exemplo 200",
                city="Olinda",
                state="PE",
                professional_summary="Engenheira de software full-stack.",
                education="Engenharia de Software - Instituto Demo",
                skills="React, TypeScript, Node.js, PostgreSQL",
                experience="4 anos em produtos web",
                linkedin_url="https://linkedin.com/in/diana-demo",
            ),
            CandidateProfile(
                user_id=candidates[2].id,
                address="Travessa Teste 50",
                city="Jaboatão",
                state="PE",
                professional_summary="Analista de segurança da informação em formação.",
                education="Sistemas de Informação - Faculdade Demo",
                skills="Security, Linux, Python, OWASP, JWT",
                experience="2 anos em suporte e hardening básico",
                linkedin_url="https://linkedin.com/in/eduardo-demo",
            ),
        ]
        db.add_all(profiles)

        jobs = [
            Job(
                recruiter_id=recruiters[0].id,
                title="Desenvolvedor Backend Python",
                description="Atuar no desenvolvimento de APIs com FastAPI e PostgreSQL.",
                requirements="Python, FastAPI, PostgreSQL, Docker, Git",
                location="Recife - PE (Híbrido)",
                employment_type=EmploymentType.FULL_TIME.value,
                salary_range="R$ 6.000 - R$ 9.000",
                status=JobStatus.OPEN.value,
            ),
            Job(
                recruiter_id=recruiters[0].id,
                title="Engenheiro de Software Frontend",
                description="Construir interfaces modernas com React e TypeScript.",
                requirements="React, TypeScript, CSS, Axios, Git",
                location="Remoto",
                employment_type=EmploymentType.REMOTE.value,
                salary_range="R$ 5.500 - R$ 8.500",
                status=JobStatus.OPEN.value,
            ),
            Job(
                recruiter_id=recruiters[1].id,
                title="Analista de Cibersegurança Júnior",
                description="Apoiar análises de vulnerabilidades e hardening.",
                requirements="Security, OWASP, Linux, Python, JWT",
                location="Recife - PE",
                employment_type=EmploymentType.FULL_TIME.value,
                salary_range="R$ 4.500 - R$ 7.000",
                status=JobStatus.OPEN.value,
            ),
            Job(
                recruiter_id=recruiters[1].id,
                title="DevOps Engineer",
                description="Automatizar pipelines e infraestrutura.",
                requirements="Docker, Kubernetes, CI/CD, Linux, AWS",
                location="Recife - PE",
                employment_type=EmploymentType.FULL_TIME.value,
                salary_range="R$ 7.000 - R$ 11.000",
                status=JobStatus.OPEN.value,
            ),
            Job(
                recruiter_id=recruiters[0].id,
                title="Estágio em Desenvolvimento Web",
                description="Apoiar time de produto em tarefas de frontend e backend.",
                requirements="JavaScript, Git, SQL, vontade de aprender",
                location="Olinda - PE",
                employment_type=EmploymentType.INTERNSHIP.value,
                salary_range="R$ 1.200 - R$ 1.800",
                status=JobStatus.CLOSED.value,
            ),
        ]
        db.add_all(jobs)
        db.flush()

        resume_specs = [
            (
                candidates[0],
                "cv_carlos_demo.docx",
                [
                    "Carlos Mendes - Desenvolvedor Backend",
                    "Skills: Python, FastAPI, PostgreSQL, Docker, Linux, REST, JWT",
                    "Experiência: APIs de recrutamento, integração com bancos relacionais.",
                    "Educação: Ciência da Computação.",
                ],
            ),
            (
                candidates[1],
                "cv_diana_demo.docx",
                [
                    "Diana Rocha - Engenheira de Software",
                    "Skills: React, TypeScript, JavaScript, Node.js, PostgreSQL, Git",
                    "Experiência: SPAs e dashboards para RH.",
                    "Educação: Engenharia de Software.",
                ],
            ),
            (
                candidates[2],
                "cv_eduardo_demo.docx",
                [
                    "Eduardo Lima - Segurança da Informação",
                    "Skills: Security, Linux, Python, OWASP, JWT, OAuth",
                    "Experiência: revisão de configurações e logs de auditoria.",
                    "Educação: Sistemas de Informação.",
                ],
            ),
        ]

        resumes: list[Resume] = []
        for candidate, filename, lines in resume_specs:
            stored = f"seed_{candidate.id.hex[:12]}_{filename}"
            path = upload_dir / stored
            size, file_hash = _write_sample_docx(path, lines)
            resume = Resume(
                candidate_id=candidate.id,
                original_filename=filename,
                stored_filename=stored,
                file_path=str(path),
                content_type=(
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                ),
                file_size=size,
                sha256_hash=file_hash,
            )
            resumes.append(resume)
        db.add_all(resumes)
        db.flush()

        applications = [
            Application(
                candidate_id=candidates[0].id,
                job_id=jobs[0].id,
                resume_id=resumes[0].id,
                status=ApplicationStatus.REVIEWING.value,
            ),
            Application(
                candidate_id=candidates[1].id,
                job_id=jobs[1].id,
                resume_id=resumes[1].id,
                status=ApplicationStatus.SUBMITTED.value,
            ),
            Application(
                candidate_id=candidates[2].id,
                job_id=jobs[2].id,
                resume_id=resumes[2].id,
                status=ApplicationStatus.INTERVIEW.value,
            ),
            Application(
                candidate_id=candidates[0].id,
                job_id=jobs[2].id,
                resume_id=resumes[0].id,
                status=ApplicationStatus.SUBMITTED.value,
            ),
        ]
        db.add_all(applications)

        db.add(
            AIAnalysis(
                resume_id=resumes[0].id,
                job_id=jobs[0].id,
                analysis_text=(
                    '{"summary":"Perfil alinhado a backend Python.",'
                    '"key_skills":["python","fastapi","postgresql","docker"],'
                    '"technologies":["python","fastapi","postgresql","docker"],'
                    '"relevant_experience":["APIs de recrutamento"],'
                    '"strengths":["Stack backend sólida"],'
                    '"gaps":["Kubernetes"],'
                    '"compatibility_notes":"Boa aderência à vaga.",'
                    '"compatibility_score":85.0}'
                ),
                extracted_skills="python, fastapi, postgresql, docker",
                compatibility_score=85.0,
            )
        )

        db.add_all(
            [
                SecurityLog(
                    user_id=admin.id,
                    event_type="auth",
                    action="login_success",
                    resource="auth",
                    success=True,
                    details="Seed demo login event",
                    ip_address="127.0.0.1",
                    user_agent="seed-script",
                ),
                SecurityLog(
                    user_id=None,
                    event_type="auth",
                    action="login_failed",
                    resource="auth",
                    success=False,
                    details="Failed login for email=unknown@example.local",
                    ip_address="127.0.0.1",
                    user_agent="seed-script",
                ),
                SecurityLog(
                    user_id=candidates[0].id,
                    event_type="resume",
                    action="resume_upload",
                    resource="resume",
                    resource_id=str(resumes[0].id),
                    success=True,
                    details="Seed resume upload",
                    ip_address="127.0.0.1",
                    user_agent="seed-script",
                ),
            ]
        )

        db.commit()
        print("Seed completed successfully.")
        print("Demo password for all users:", DEMO_PASSWORD)
    finally:
        db.close()


if __name__ == "__main__":
    seed()
