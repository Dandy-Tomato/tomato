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
public class CompanyInsertTasklet implements Tasklet {

    private final JdbcTemplate jdbcTemplate;

    @Override
    public RepeatStatus execute(StepContribution contribution, ChunkContext chunkContext) throws Exception {

        jdbcTemplate.update("""
                INSERT INTO companies (company_id, name, domain_id, created_at, updated_at, search_name)
                SELECT
                    s.company_id,
                    s.name,
                    s.domain_id,
                    COALESCE(s.created_at, now()),
                    COALESCE(s.updated_at, now()),
                    s.search_name
                FROM companies_staging s
                WHERE s.name IS NOT NULL
                ON CONFLICT (name) DO NOTHING;
                """);

        return RepeatStatus.FINISHED;
    }

}
