package site.to_mato.batch.job;

import lombok.RequiredArgsConstructor;
import org.springframework.batch.core.Job;
import org.springframework.batch.core.Step;
import org.springframework.batch.core.job.builder.JobBuilder;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
@RequiredArgsConstructor
public class CompanyImportJobConfig {

    private final JobRepository jobRepository;
    private final Step companyStagingStep;
    private final Step companyInsertStep;
    private final Step skillInsertStep;
    private final Step companySkillStagingStep;
    private final Step companySkillInsertStep;
    private final Step stagingTruncateStep;

    @Bean
    public Job companyImportJob() {
        return new JobBuilder("companyImportJob", jobRepository)
                .start(companyStagingStep)      // 1. company staging 적재
                .next(companyInsertStep)        // 2. company insert
                .next(skillInsertStep)          // 3. skill insert
                .next(companySkillStagingStep)  // 4. company skill staging 적재
                .next(companySkillInsertStep)   // 5. company skill insert
                .next(stagingTruncateStep)      // 6. staging tables truncate
                .build();
    }
}
