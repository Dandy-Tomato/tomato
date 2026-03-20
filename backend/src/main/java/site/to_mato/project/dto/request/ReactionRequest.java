package site.to_mato.project.dto.request;

import jakarta.validation.constraints.NotNull;
import site.to_mato.project.entity.enums.Reaction;

public record ReactionRequest(

        @NotNull
        Reaction reaction,
        Long version

) {}
