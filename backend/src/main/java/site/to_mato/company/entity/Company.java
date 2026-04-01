package site.to_mato.company.entity;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import site.to_mato.catalog.entity.Domain;
import site.to_mato.common.entity.BaseEntity;

import java.util.ArrayList;
import java.util.List;

@Getter
@Entity
@Table(name = "companies")
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Company extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "company_id")
    private Long id;

    @Column(nullable = false, unique = true)
    private String name;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "domain_id")
    private Domain domain;

    @Column(name = "search_name")
    private String searchName;

    @OneToMany(mappedBy = "company")
    private List<CompanySkill> companySkills = new ArrayList<>();

    @Builder(access = AccessLevel.PRIVATE)
    private Company(String name, Domain domain) {
        this.name = name;
        this.domain = domain;
    }

    public void updateSearchName(String searchName) {
        this.searchName = searchName;
    }
}
