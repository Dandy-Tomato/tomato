package site.to_mato.batch.writer;

import jakarta.persistence.EntityManagerFactory;
import lombok.RequiredArgsConstructor;
import org.springframework.batch.item.database.JpaItemWriter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import site.to_mato.batch.entity.CompanyStaging;

@Configuration
@RequiredArgsConstructor
public class CompanyStagingWriterConfig {

    private final EntityManagerFactory entityManagerFactory;

    @Bean
    public JpaItemWriter<CompanyStaging> companyStagingWriter() {
        JpaItemWriter<CompanyStaging> writer = new JpaItemWriter<>();
        writer.setEntityManagerFactory(entityManagerFactory);
        return writer;
    }
}
