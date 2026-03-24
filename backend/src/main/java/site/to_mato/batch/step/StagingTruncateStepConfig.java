package site.to_mato.batch.step;

import lombok.RequiredArgsConstructor;
import org.springframework.batch.core.Step;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.batch.core.step.builder.StepBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.transaction.PlatformTransactionManager;
import site.to_mato.batch.tasklet.StagingTruncateTasklet;

@Configuration
@RequiredArgsConstructor
public class StagingTruncateStepConfig {

    private final JobRepository jobRepository;
    private final PlatformTransactionManager transactionManager;

    @Bean
    public Step stagingTruncateStep(StagingTruncateTasklet tasklet) {
        return new StepBuilder("stagingTruncateStep", jobRepository)
                .tasklet(tasklet, transactionManager)
                .build();
    }
}
