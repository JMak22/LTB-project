operational_metrics <- function() {
  library(readr)
  library(ggplot2)
  library(dplyr)

  df <- read_csv(here::here("cleaned_data", "operational_metrics.csv"))

  glimpse(df)

  df |>
    ggplot() +
    aes(x = value, y = report_id) +
    geom_col(orientation = "y") +
    labs(
      title = "operational metrics",
      subtitle = "1998-2025",
      caption = "Source:<add source>",
      x = "applications"
    ) +
    scale_x_continuous(
      labels = scales::label_number(scale_cut = scales::cut_short_scale())
    ) +
    facet_wrap(~metric_id) +
    theme_minimal()
}
# operational_metrics()
