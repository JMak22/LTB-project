l_single_type_avg_days_chart <- function() {
  library(readr)
  library(dplyr)
  library(ggplot2)

  df <- read_csv(here::here("cleaned_data", "l_single_type_avg_days_chart.csv"))

  glimpse(df)

  df |>
    mutate(
      app_type = factor(
        app_type,
        levels = c("L2", "L3", "L4", "L5", "L6", "L7", "L8", "L9", "L10")
      )
    ) |>
    ggplot() +
    geom_col(
      aes(x = avg_days, y = report_id, fill = avg_days > performance_standard),
      orientation = "y",
      show.legend = FALSE
    ) +
    scale_fill_manual(values = c(`TRUE` = "#df0000", `FALSE` = "#006fdf")) +
    geom_point(
      aes(x = performance_standard, y = report_id),
      shape = "|",
      size = 4
    ) +
    facet_wrap(~app_type, nrow = 1) +
    theme_minimal() +
    labs(
      title = "Single Type Average Days",
      subtitle = "2015-2026 (per quarter)",
      caption = "Source:<add source>"
    )
}
# l_single_type_avg_days_chart()
