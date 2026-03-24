package site.to_mato.batch.tasklet;

import lombok.RequiredArgsConstructor;
import org.springframework.batch.core.StepContribution;
import org.springframework.batch.core.scope.context.ChunkContext;
import org.springframework.batch.core.step.tasklet.Tasklet;
import org.springframework.batch.repeat.RepeatStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class CompanySkillInsertTasklet implements Tasklet {

    private final JdbcTemplate jdbcTemplate;

    @Override
    public RepeatStatus execute(StepContribution contribution, ChunkContext chunkContext) throws Exception {

        jdbcTemplate.update("""
            INSERT INTO company_skills (company_id, skill_id)
            SELECT DISTINCT
                c.company_id,
                css.skill_id
            FROM company_skills_staging css
            JOIN companies_staging cs
                ON cs.company_id = css.company_id
            JOIN companies c
                ON c.name = cs.name
            ON CONFLICT (company_id, skill_id) DO NOTHING
        """);

        return RepeatStatus.FINISHED;
    }
}
