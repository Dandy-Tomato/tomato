package site.to_mato.topic.dto.request;

import jakarta.validation.constraints.NotNull;
import site.to_mato.topic.entity.enums.Reaction;

public record ReactionRequest(

        @NotNull
        Reaction reaction

) {}
