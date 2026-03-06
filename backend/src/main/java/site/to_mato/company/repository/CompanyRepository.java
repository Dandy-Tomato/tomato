package site.to_mato.company.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import site.to_mato.company.entity.Company;

public interface CompanyRepository extends JpaRepository<Company, Long> {
}
