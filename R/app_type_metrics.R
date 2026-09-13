app_type_metrics <- function() {
  library(ggplot2)
  library(readr)
  library(dplyr)
  library(tidyr)

  read_csv(here::here("cleaned_data", "app_type_metrics.csv")) |>
    # values are characters, conver to numerical
    mutate(value = as.integer(value)) |>
    # drop the "-"/"not reported" rows
    drop_na() |>
    ggplot() +
    aes(x = value, y = report_id) +
    geom_col(orientation = "y", aes(fill = app_code), show.legend = FALSE) +
    # obvious that Termination for non-payment of rent is much  pmopre prevalent thaan anything else
    # facet_wrap(~description, scales = "fixed")+
    # free x-ais to make other app codes visible
    facet_wrap(~description, scales = "free_x") +
    theme_minimal()
}

# app_type_metrics()
