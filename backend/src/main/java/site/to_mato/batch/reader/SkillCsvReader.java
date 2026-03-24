package site.to_mato.batch.reader;

import org.springframework.batch.core.configuration.annotation.StepScope;
import org.springframework.batch.item.file.FlatFileItemReader;
import org.springframework.batch.item.file.builder.FlatFileItemReaderBuilder;
import org.springframework.batch.item.file.mapping.FieldSetMapper;
import org.springframework.batch.item.file.transform.FieldSet;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.FileSystemResource;
import site.to_mato.batch.entity.CompanySkillStaging;
import site.to_mato.catalog.entity.Skill;

@Configuration
public class SkillCsvReader {

    @Bean
    @StepScope
    public FlatFileItemReader<Skill> skillReader(
            @Value("${batch.file.skill}") String filePath
    ) {
        return new FlatFileItemReaderBuilder<Skill>()
                .name("skillReader")
                .resource(new FileSystemResource(filePath))
                .delimited()
                .names("skill_id", "front_name")
                .fieldSetMapper(skillFieldSetMapper())
                .linesToSkip(1)     // header
                .build();

    }

    @Bean
    public FieldSetMapper<Skill> skillFieldSetMapper() {
        return fieldSet -> Skill.builder()
                .id(fieldSet.readLong("skill_id"))
                .name(fieldSet.readString("front_name"))
                .build();
    }

}
