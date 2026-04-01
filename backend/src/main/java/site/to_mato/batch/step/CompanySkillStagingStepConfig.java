package site.to_mato.batch.step;

import lombok.RequiredArgsConstructor;
import org.springframework.batch.core.Step;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.batch.core.step.builder.StepBuilder;
import org.springframework.batch.item.database.JpaItemWriter;
import org.springframework.batch.item.file.FlatFileItemReader;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.transaction.PlatformTransactionManager;
import site.to_mato.batch.entity.CompanySkillStaging;

@Configuration
@RequiredArgsConstructor
public class CompanySkillStagingStepConfig {

    private final JobRepository jobRepository;
    private final PlatformTransactionManager transactionManager;
    private final FlatFileItemReader<CompanySkillStaging> companySkillStagingReader;
    private final JpaItemWriter<CompanySkillStaging> companySkillStagingWriter;

    @Bean
    public Step companySkillStagingStep() {
        return new StepBuilder("companySkillStagingStep", jobRepository)
                .<CompanySkillStaging, CompanySkillStaging>chunk(1000, transactionManager)
                .reader(companySkillStagingReader)
                .writer(companySkillStagingWriter)
                .build();
    }

}
