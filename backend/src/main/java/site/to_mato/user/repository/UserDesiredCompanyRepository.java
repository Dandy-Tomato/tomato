package site.to_mato.user.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import site.to_mato.user.entity.UserDesiredCompany;

public interface UserDesiredCompanyRepository extends JpaRepository<UserDesiredCompany, Long> {
}
