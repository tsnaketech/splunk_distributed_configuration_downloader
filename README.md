# Distributed Configuration Downloader

This repo is designed to download configuration elements that can be found in the Enterprise Security interface under General setting.

## Requirements

- Python 3.x
- Splunk Enterprise
- Splunk Enterprise Security
- Network access to the central configuration repository

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/tsnaketech/splunk_distributed_configuration_downloader.git
    ```
2. Navigate to the project directory:
    ```sh
    cd splunk_distributed_configuration_downloader
    ```
3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Configure the settings in `.env` file or in `.conf`,`.ini`,`.yaml`,`.yml` configuration file to match your environment.
2. Run the downloader script:
    ```sh
    python splunk_distributed_configuration_downloader --config config.yaml
    ```

    ```sh
    python splunk_distributed_configuration_downloader\downloader.py --config config.yaml
    ```
    
    Possible parameters:
    - `--routine` (`-r`): Routine to execute. Choices are `index_time_properties`, `on_prem`.
    - `--extension` (`-e`): Extension for the downloaded file. Choices are `spl`, `tar.gz`, `tgz`.

## Configuration

Sample configuration files are available with a `.sample` extension in `sample` folder. You can use these as a starting point for your own configuration:

- `sample\.env.sample`
- `sample\config.ini.sample`
- `sample\config.yaml.sample`

Make sure to customize these files to match your environment before running the downloader script.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss your ideas.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.