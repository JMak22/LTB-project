financial_metrics <- function() {
  library(readr)
  library(dplyr)
  library(ggplot2)
  library(scales)
  df <- read_csv(here::here("cleaned_data", "financial_metrics.csv"))

  glimpse(df)

  df |>
    ggplot() +
    aes(x = value, y = report_id) +
    geom_col() +
    scale_x_continuous(labels = label_currency()) +
    facet_wrap(~metric_id, scales = "free_x") +
    labs(
      title = "Financial Metrics",
      subtiltle = "1990-2016",
      caption = "Source: <add source>"
    ) +
    theme_minimal()
}

# only execute if run as standalone
# financial_metrics()
