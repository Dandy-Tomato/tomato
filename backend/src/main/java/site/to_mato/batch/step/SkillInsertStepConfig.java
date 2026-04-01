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
import site.to_mato.catalog.entity.Skill;

@Configuration
@RequiredArgsConstructor
public class SkillInsertStepConfig {

    private final JobRepository jobRepository;
    private final PlatformTransactionManager transactionManager;
    private final FlatFileItemReader<Skill> skillReader;
    private final JpaItemWriter<Skill> skillWriter;

    @Bean
    public Step skillInsertStep() {
        return new StepBuilder("skillInsertStep", jobRepository)
                .<Skill, Skill>chunk(1000, transactionManager)
                .reader(skillReader)
                .writer(skillWriter)
                .build();
    }

}
