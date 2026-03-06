package site.to_mato.user.entity;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import site.to_mato.company.entity.Company;

@Getter
@Entity
@Table(
        name = "user_desired_companies",
        uniqueConstraints = {
                @UniqueConstraint(
                        name = "uk_user_company",
                        columnNames = {"user_id", "company_id"}
                )
        }
)
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class UserDesiredCompany {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "user_desired_company_id")
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "user_id")
    private User user;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "company_id")
    private Company company;

    @Builder
    private UserDesiredCompany(User user, Company company) {
        this.user = user;
        this.company = company;
    }

    public static UserDesiredCompany of(User user, Company company) {
        return UserDesiredCompany.builder()
                .user(user)
                .company(company)
                .build();
    }
}