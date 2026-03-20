package site.to_mato.project.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

import java.time.LocalDateTime;
import java.util.List;

public final class ProjectRequestDto {

    private ProjectRequestDto() {
    }

    public record Create(
            @NotBlank(message = "프로젝트 이름은 필수입니다.")
            @Size(max = 255, message = "프로젝트 이름은 255자 이하여야 합니다.")
            String name,

            String description,

            LocalDateTime startedAt,
            LocalDateTime dueAt,

            @NotNull(message = "domainIds는 필수입니다.")
            List<Long> domainIds
    ) {
    }

    public record Update(
            @Size(max = 255, message = "프로젝트 이름은 255자 이하여야 합니다.")
            String name,
            String description,
            LocalDateTime startedAt,
            LocalDateTime dueAt,
            List<Long> domainIds
    ) {
    }

    public record ConfirmTopic(
            @NotNull(message = "confirmedChildTopicId는 필수입니다.")
            Long confirmedChildTopicId
    ) {
    }

    public record Join(
            @NotBlank(message = "inviteCode는 필수입니다.")
            String inviteCode
    ) {
    }

    public record TransferOwner(
            @NotNull(message = "newOwnerUserId는 필수입니다.")
            Long newOwnerUserId
    ) {
    }
}