t_single_type_avg_days_chart <- function() {
  library(readr)
  library(dplyr)

  df <- read_csv(here::here("cleaned_data", "t_single_type_avg_days_chart.csv"))

  glimpse(df)

  df |>
    tidyr::drop_na() |>
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

# t_single_type_avg_days_chart()
