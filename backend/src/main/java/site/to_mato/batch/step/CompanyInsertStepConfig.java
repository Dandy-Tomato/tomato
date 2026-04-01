package site.to_mato.batch.step;

import lombok.RequiredArgsConstructor;
import org.springframework.batch.core.Step;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.batch.core.step.builder.StepBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.transaction.PlatformTransactionManager;
import site.to_mato.batch.tasklet.CompanyInsertTasklet;

@Configuration
@RequiredArgsConstructor
public class CompanyInsertStepConfig {

    private final JobRepository jobRepository;
    private final PlatformTransactionManager transactionManager;

    @Bean
    public Step companyInsertStep(CompanyInsertTasklet tasklet) {
        return new StepBuilder("companyInsertStep", jobRepository)
                .tasklet(tasklet, transactionManager)
                .build();
    }

}
