package site.to_mato.company.repository;

import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import site.to_mato.company.entity.Company;

import java.util.List;

public interface CompanyRepository extends JpaRepository<Company, Long> {

    List<Company> findBySearchNameContainingIgnoreCase(String keyword, Pageable pageable);

    List<Company> findTop10BySearchNameStartingWithIgnoreCase(String keyword);

    List<Company> findBySearchNameIsNull();

}
