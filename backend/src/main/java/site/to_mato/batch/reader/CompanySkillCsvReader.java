package site.to_mato.batch.reader;

import org.springframework.batch.core.configuration.annotation.StepScope;
import org.springframework.batch.item.file.FlatFileItemReader;
import org.springframework.batch.item.file.builder.FlatFileItemReaderBuilder;
import org.springframework.batch.item.file.mapping.FieldSetMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.FileSystemResource;
import site.to_mato.batch.entity.CompanySkillStaging;

import java.io.File;

@Configuration
public class CompanySkillCsvReader {

    @Bean
    @StepScope
    public FlatFileItemReader<CompanySkillStaging> companySkillStagingReader(
            @Value("${batch.file.root}") String rootPath,
            @Value("${batch.file.company}") String fileName,
            @Value("#{jobParameters['date']}") String date
    ) {
        String fullPath = rootPath + date + File.separator + fileName;

        return new FlatFileItemReaderBuilder<CompanySkillStaging>()
                .name("companySkillStagingReader")
                .resource(new FileSystemResource(fullPath))
                .delimited()
                .names("company_skill_id", "company_id", "skill_id")
                .fieldSetMapper(companySkillFieldSetMapper())
                .linesToSkip(1)     // header
                .build();

    }

    @Bean
    public FieldSetMapper<CompanySkillStaging> companySkillFieldSetMapper() {
        return fieldSet -> CompanySkillStaging.builder()
                .companySkillId(fieldSet.readLong("company_skill_id"))
                .companyId(fieldSet.readLong("company_id"))
                .skillId(fieldSet.readLong("skill_id"))
                .build();
    }
}
