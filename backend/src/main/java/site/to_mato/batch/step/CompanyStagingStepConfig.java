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
import site.to_mato.batch.entity.CompanyStaging;
import site.to_mato.batch.processor.CompanyStagingProcessor;

@Configuration
@RequiredArgsConstructor
public class CompanyStagingStepConfig {

    private final JobRepository jobRepository;
    private final PlatformTransactionManager transactionManager;
    private final FlatFileItemReader<CompanyStaging> companyStagingReader;
    private final CompanyStagingProcessor companyStagingProcessor;
    private final JpaItemWriter<CompanyStaging> companyStagingWriter;

    @Bean
    public Step companyStagingStep() {
        return new StepBuilder("companyStagingStep", jobRepository)
                .<CompanyStaging, CompanyStaging>chunk(1000, transactionManager)
                .reader(companyStagingReader)
                .processor(companyStagingProcessor)
                .writer(companyStagingWriter)
                .build();
    }

}
