# Distributed Configuration Downloader

This project is designed to download and manage distributed configurations for Splunk. It ensures that all configurations are up-to-date and synchronized across multiple instances.

## Features

- Download configurations from a central repository
- Synchronize configurations across multiple Splunk instances
- Ensure consistency and up-to-date configurations

## Requirements

- Python 3.x
- Splunk SDK for Python
- Network access to the central configuration repository

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/distributed_configuration_downloader.git
    ```
2. Navigate to the project directory:
    ```sh
    cd distributed_configuration_downloader
    ```
3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Configure the settings in `.env` file or in `.conf`,`.ini`,`.yaml`,`.yml` configuration file to match your environment.
2. Run the downloader script:
    ```sh
    python downloader.py -config config.yaml
    ```
    
    Possible parameters:
    - `--routine` (`-r`): Routine to execute. Choices are `index_time_properties`, `on_prem`.
    - `--extension` (`-e`): Extension for the downloaded file. Choices are `spl`, `tar.gz`, `tgz`.

## Configuration

Sample configuration files are available with a `.sample` extension. You can use these as a starting point for your own configuration:

- `.env.sample`
- `config.ini.sample`
- `config.yaml.sample`

Make sure to customize these files to match your environment before running the downloader script.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss your ideas.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.