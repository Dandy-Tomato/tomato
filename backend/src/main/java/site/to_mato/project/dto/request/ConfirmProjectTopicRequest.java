package site.to_mato.project.dto.request;

import jakarta.validation.constraints.NotNull;

public record ConfirmProjectTopicRequest(
        @NotNull Long childTopicId
) {
}
