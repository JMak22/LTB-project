library(readr)
library(ggplot2)
library(tidytext)
library(dplyr)

combo_application_summary <- function() {
  df <- read_csv(here::here("cleaned_data", "combo_application_summary.csv"))
  glimpse(df)
  df |>
    mutate(
      combo_family = factor(
        combo_family,
        levels = c("Landlord", "Tenant", "Mixed", "Other")
      )
    ) |>
    ggplot() +
    aes(
      x = count_per_period,
      y = reorder_within(
        x = app_combo,
        by = count_per_period,
        within = combo_family
      ),
      fill = combo_family
    ) +
    scale_y_reordered() +
    geom_col(orientation = "y", show.legend = FALSE) +
    facet_wrap(~combo_family, scales = "free_y", nrow = 1) +
    labs(
      title = "Combo Application Summary",
      subtitle = "<subtitle goes here>",
      caption = "Source:<source goes here>",
      y = "combo_family"
    ) +
    theme_minimal()
}
