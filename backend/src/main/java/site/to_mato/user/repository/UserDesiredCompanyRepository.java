package site.to_mato.user.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import site.to_mato.catalog.entity.Domain;
import site.to_mato.user.entity.User;
import site.to_mato.user.entity.UserDesiredCompany;

import java.util.List;

public interface UserDesiredCompanyRepository extends JpaRepository<UserDesiredCompany, Long> {

    List<UserDesiredCompany> findAllByUser_Id(Long userId);

    void deleteAllByUser(User user);

    @Query("""
        select distinct udc.company.id
        from UserDesiredCompany udc
        where udc.user.id = :userId
          and udc.company is not null
    """)
    List<Long> findDistinctCompanyIdsByUserId(@Param("userId") Long userId);

    @Query("""
        select distinct c.domain
        from UserDesiredCompany udc
        join udc.company c
        where udc.user.id = :userId
          and c.domain is not null
    """)
    List<Domain> findDistinctDomainsByUserId(@Param("userId") Long userId);
}
