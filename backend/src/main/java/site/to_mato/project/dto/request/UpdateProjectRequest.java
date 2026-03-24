package site.to_mato.project.dto.request;

import jakarta.validation.constraints.Size;

import java.time.LocalDate;
import java.util.List;

public record UpdateProjectRequest(

        @Size(max = 100, message = "프로젝트명은 100자 이하여야 합니다.")
        String name,

        @Size(max = 1000, message = "프로젝트 설명은 1000자 이하여야 합니다.")
        String description,

        LocalDate startedAt,
        LocalDate dueAt,

        List<Long> techSkillIds,
        List<Long> domainIds
) {
}
