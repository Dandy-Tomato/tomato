package site.to_mato.batch.writer;


import jakarta.persistence.EntityManagerFactory;
import lombok.RequiredArgsConstructor;
import org.springframework.batch.item.database.JpaItemWriter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import site.to_mato.batch.entity.CompanySkillStaging;

@Configuration
@RequiredArgsConstructor
public class CompanySkillStagingWriterConfig {

    private final EntityManagerFactory entityManagerFactory;

    @Bean
    public JpaItemWriter<CompanySkillStaging> companySkillStagingWriter() {
        JpaItemWriter<CompanySkillStaging> writer = new JpaItemWriter<>();
        writer.setEntityManagerFactory(entityManagerFactory);
        return writer;
    }
}
