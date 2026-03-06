package site.to_mato.user.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import site.to_mato.user.entity.User;
import site.to_mato.user.entity.UserDesiredCompany;

import java.util.List;

public interface UserDesiredCompanyRepository extends JpaRepository<UserDesiredCompany, Long> {

    List<UserDesiredCompany> findAllByUser_Id(Long userId);

    void deleteAllByUser(User user);
}
