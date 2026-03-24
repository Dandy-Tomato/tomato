package site.to_mato.batch.entity;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Getter
@Entity
@Table(name = "companies_staging")
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class CompanyStaging {

    @Id
    @Column(name = "company_id")
    private Long companyId; // CSV 원본 ID (PK로 사용)

    @Column(name = "name")
    private String name;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Column(name = "domain_id")
    private Long domainId;

    @Column(name = "search_name")
    private String searchName;

    @Builder
    public CompanyStaging(Long companyId, String name, LocalDateTime createdAt, LocalDateTime updatedAt, Long domainId) {
        this.companyId = companyId;
        this.name = name;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.domainId = domainId;
    }

    public void updateSearchName(String searchName) {
        this.searchName = searchName;
    }

}
