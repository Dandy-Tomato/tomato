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
import site.to_mato.batch.entity.CompanyStaging;

import java.io.File;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

@Configuration
public class CompanyCsvReader {

    @Bean
    @StepScope
    public FlatFileItemReader<CompanyStaging> companyStagingReader(
            @Value("${batch.file.root}") String rootPath,
            @Value("${batch.file.company}") String fileName,
            @Value("#{jobParameters['date']}") String date
    ) {
        String fullPath = rootPath + date + File.separator + fileName;

        return new FlatFileItemReaderBuilder<CompanyStaging>()
                .name("companyStagingReader")
                .resource(new FileSystemResource(fullPath))
                .delimited()
                .names("company_id", "name", "created_at", "updated_at", "domain_id")
                .fieldSetMapper(companyFieldSetMapper())
                .linesToSkip(1)     // header
                .build();

    }

    @Bean
    public FieldSetMapper<CompanyStaging> companyFieldSetMapper() {
        return new FieldSetMapper<>() {

            private final DateTimeFormatter formatter =
                    DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

            @Override
            public CompanyStaging mapFieldSet(FieldSet fieldSet) {

                return CompanyStaging.builder()
                        .companyId(fieldSet.readLong("company_id"))
                        .name(fieldSet.readString("name"))
                        .createdAt(LocalDateTime.parse(
                                fieldSet.readString("created_at"), formatter))
                        .updatedAt(LocalDateTime.parse(
                                fieldSet.readString("updated_at"), formatter))
                        .domainId(fieldSet.readLong("domain_id"))
                        .build();
            }
        };
    }

}
