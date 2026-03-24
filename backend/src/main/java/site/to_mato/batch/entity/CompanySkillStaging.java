package site.to_mato.batch.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@Entity
@Table(name = "company_skills_staging")
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class CompanySkillStaging {

    @Id
    @Column(name = "company_skill_id")
    private Long companySkillId; // CSV 원본 ID (PK로 사용)

    @Column(name = "company_id")
    private Long companyId;     // CSV 원본 ID

    @Column(name = "skill_id")
    private Long skillId;

    @Builder
    public CompanySkillStaging(Long companySkillId, Long companyId, Long skillId) {
        this.companySkillId = companySkillId;
        this.companyId = companyId;
        this.skillId = skillId;
    }
}
