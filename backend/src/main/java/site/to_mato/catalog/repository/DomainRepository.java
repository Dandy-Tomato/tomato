package site.to_mato.catalog.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import site.to_mato.catalog.entity.Domain;

public interface DomainRepository extends JpaRepository<Domain, Long> {
}
