package site.to_mato.project.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

import java.time.LocalDate;
import java.util.List;

public record CreateProjectRequest(

        @NotBlank(message = "프로젝트명은 필수입니다.")
        @Size(max = 100, message = "프로젝트명은 100자 이하여야 합니다.")
        String name,
        @Size(max = 1000, message = "프로젝트 설명은 1000자 이하여야 합니다.")
        String description,
        @NotNull(message = "프로젝트 시작일은 필수입니다.")
        LocalDate startedAt,
        @NotNull(message = "프로젝트 종료일은 필수입니다.")
        LocalDate dueAt,

        List<Long> techSkillIds,
        List<Long> domainIds
) {
}
